from django.core import mail
from django.test import TestCase
from eventex.subscriptions.forms import SubscriptionForm

class SubscriptionTest(TestCase):
    
    def setUp(self):
        self.response = self.client.get('/inscricao/')
    
    def test_get(self):
        '''Get /inscricao/ must return status code 200'''
        self.assertEqual(200, self.response.status_code)
    
    
    def test_template(self):
        '''Must use subscriptions/subscription_form.html'''
        self.assertTemplateUsed(self.response,
                                'subscriptions/subscription_form.html')
                            
    
    def test_hmtl(self):
        '''Html must contains input tags'''
        self.assertContains(self.response, '<form')
        self.assertContains(self.response, '<input', 6)
        self.assertContains(self.response, 'type="text"', 3)
        self.assertContains(self.response, 'type="email"')
        self.assertContains(self.response, 'type="submit"')
        
        
    def test_csrf(self):
        """Html must contains test_csrf"""
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        
        
    def test_has_form(self):
        '''Context must have subscription form'''
        form = self.response.context['form']
        self.assertIsInstance(form, SubscriptionForm)
        
    
    def test_form_has_fields(self):
        '''Form must have 4 fields'''
        form = self.response.context['form']
        self.assertSequenceEqual(['name', 'cpf', 'email', 'phone'], 
                                 list(form.fields))
    
    
class SubscribePost(TestCase):
    def setUp(self):
        data = dict(name='Henrique Bastos', cpf=12345678901,
                    email='henrique@bastos.net', phone='51-9580-9174')
        self.response = self.client.post('/inscricao/', data)
        self.email = mail.outbox[0]
        
    def test_post(self):
        '''Valid post should redirect to /inscricao/'''
        self.assertEqual(302, self.response.status_code)
        
    
    def test_send_subscribe_email(self):
        self.assertEqual(1, len(mail.outbox))
    
    
    def test_subscription_email_subject(self):
        expect = 'Confirmação da Inscrição'
        self.assertEqual(expect, self.email.subject)
    
    
    def test_subscription_email_from(self):
        expect = 'contato@eventex.com.br'
        self.assertEqual(expect, self.email.from_email)
        
    
    def test_subscription_email_to(self):
        expect = ['contato@eventex.com.br', 'henrique@bastos.net']
        self.assertEqual(expect, self.email.to)
        
    
    def test_subscription_email_body(self):
        self.assertIn('Henrique Bastos', self.email.body)
        self.assertIn('12345678901', self.email.body)
        self.assertIn('henrique@bastos.net', self.email.body)
        self.assertIn('51-9580-9174', self.email.body)


class SubscribeInvalidPost(TestCase):
    
    def setUp(self):
        self.response = self.client.post('/inscricao/', {})
        
        
    def test_post(self):
        '''Invalid post should not redirect'''
        self.assertEqual(200, self.response.status_code)
        
    
    def teste_template(self):
        self.assertTemplateUsed(self.response, 'subscriptions/subscription_form.html')
    
    
    def test_has_form(self):
        form = self.response.context['form']
        self.assertIsInstance(form, SubscriptionForm)
        
    
    def test_form_has_errors(self):
        form = self.response.context['form']
        self.assertTrue(form.errors)


class SubscribeSuccessMessage(TestCase):
    def test_message(self):
        data = dict(name='Henrique Bastos', email='henrique@bastos.net',
                    phone='51-9580-9174', cpf='12345678901')
        response = self.client.post('/inscricao/', data, follow=True)
        self.assertContains(response, 'Inscrição Realizada.')