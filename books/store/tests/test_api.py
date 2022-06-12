import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=15, author_name='Author 2', owner=self.user)
        self.book_3 = Book.objects.create(name='Test book Author 1', price=15, author_name='Author 3', owner=self.user)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        print(response.data)

    def test_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BooksSerializer([self.book_1, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        print(response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())  # работает

        url = reverse('book-list')
        data = {
            'name': 'Programming in python 3',
            'price': '150.00',
            'author_name': 'Mark Summerfield'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)  # прикрутили тестового пользователя
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        self.assertEqual(4, Book.objects.all().count())  # работает
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 575,
            'author_name': self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)  # прикрутили тестового пользователя
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()  # обновление элемента в базе данных
        self.assertEqual(575, self.book_1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')

        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': 25,
            'author_name': self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)  # прикрутили тестового пользователя
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db()  # обновление элемента в базе данных
        self.assertEqual(25, self.book_1.price)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())

        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)  # прикрутили тестового пользователя
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        self.assertEqual(2, Book.objects.all().count())  # работает

    def test_get_element(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)  # прикрутили тестового пользователя
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(self.book_1.id, response.data['id'])

