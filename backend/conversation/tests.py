from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Conversation, Message


class ConversationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.conversation = Conversation.objects.create(title='Test Conversation')
        self.conversation.participants.add(self.user)
    
    def test_conversation_creation(self):
        self.assertEqual(self.conversation.title, 'Test Conversation')
        self.assertTrue(self.user in self.conversation.participants.all())
        self.assertTrue(self.conversation.is_active)
    
    def test_message_ordering(self):
        # Create messages in reverse order
        msg3 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            role='user',
            content='Third message',
            order_index=3
        )
        msg1 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            role='user',
            content='First message',
            order_index=1
        )
        msg2 = Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            role='user',
            content='Second message',
            order_index=2
        )
        
        # Messages should be ordered by order_index
        messages = list(self.conversation.messages.all())
        self.assertEqual(messages[0].order_index, 1)
        self.assertEqual(messages[1].order_index, 2)
        self.assertEqual(messages[2].order_index, 3)


class ConversationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.conversation = Conversation.objects.create(title='Test Conversation')
        self.conversation.participants.add(self.user)
    
    def test_create_conversation(self):
        data = {'title': 'New Conversation'}
        response = self.client.post('/api/conversations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 2)
    
    def test_add_message(self):
        data = {
            'conversation': self.conversation.id,
            'role': 'user',
            'content': 'Hello, this is a test message'
        }
        response = self.client.post('/api/messages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
    
    def test_reconstruct_conversation(self):
        # Create some messages
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            role='user',
            content='Hello',
            order_index=1
        )
        Message.objects.create(
            conversation=self.conversation,
            sender=self.user,
            role='assistant',
            content='Hi there!',
            order_index=2
        )
        
        response = self.client.get(f'/api/conversations/{self.conversation.id}/reconstruct/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['messages']), 2)
        self.assertEqual(response.data['messages'][0]['order'], 1)
        self.assertEqual(response.data['messages'][1]['order'], 2)
