from datetime import datetime

from django.db import models
from django.test import TestCase

from result_handler import ResultHandler

    
class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    dob = models.DateField()
    
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author)
    
class Coffee(models.Model):
    brand = models.CharField(max_length=255, db_column="name")


class ResultHandlerTests(TestCase):
    
    def setUp(self):
        self.authors = []
        self.books = []
        self.coffees = []
        
        self.authors.append(Author.objects.create(
            first_name="Joe",
            last_name="Smith",
            dob=datetime(year=1950, month=9, day=20),
        ))
        self.authors.append(Author.objects.create(
            first_name="Jill",
            last_name="Doe",
            dob=datetime(year=1920, month=4, day=2),
        ))
        self.authors.append(Author.objects.create(
            first_name="Bob",
            last_name="Smith",
            dob=datetime(year=1986, month=1, day=25),
        ))
        self.authors.append(Author.objects.create(
            first_name="Bill",
            last_name="Jones",
            dob=datetime(year=1932, month=5, day=10),
        ))
        
        self.books.append(Book.objects.create(
            title = 'The awesome book',
            author = self.authors[0],
        ))

        self.books.append(Book.objects.create(
            title = 'The horrible book',
            author = self.authors[0],
        ))

        self.books.append(Book.objects.create(
            title = 'Another awesome book',
            author = self.authors[0],
        ))
        
        self.books.append(Book.objects.create(
            title = 'Some other book',
            author = self.authors[2],
        ))
        
        self.coffees.append(Coffee.objects.create(brand="dunkin doughnuts"))
        self.coffees.append(Coffee.objects.create(brand="starbucks"))
        
    def assertHandled(self, handled, orig):
        self.assertEqual(len(handled), len(orig))
        for index, item in enumerate(handled):
            self.assertEqual(item, orig[index])
        
    def testSimpleHandler(self):
        query = "SELECT * FROM result_handler_author"
        handled_authors = ResultHandler(Author, query)
        self.assertHandled(handled_authors, self.authors)
        
    def testFkeyHandler(self):
        query = "SELECT * FROM result_handler_book"
        handled_books = ResultHandler(Book, query)
        self.assertHandled(handled_books, self.books)
        
    def testDBColumnHandler(self):
        query = "SELECT * FROM result_handler_coffee"
        handled_coffees = ResultHandler(Coffee, query)
        self.assertHandled(handled_coffees, self.coffees)
        
    def testOrderHandler(self):
        selects = (
            ('dob, last_name, first_name, id'),
            ('last_name, dob, first_name, id'),
            ('first_name, last_name, dob, id'),
        )
        
        for select in selects:
            query = "SELECT %s FROM result_handler_author" % select
            handled_authors = ResultHandler(Author, query)
            self.assertHandled(handled_authors, self.authors)
            
    def testTranslations(self):
        query = "SELECT first_name AS first, last_name AS last, dob, id FROM result_handler_author"
        translations = (
            ('first', 'first_name'),
            ('last', 'last_name'),
        )
        handled_authors = ResultHandler(Author, query, translations=translations)
        
    def testParams(self):
        query = "SELECT * FROM result_handler_author WHERE first_name = %s"
        params = [self.authors[2].first_name]
        handled_authors = ResultHandler(Author, query, params=params)
        self.assertEqual(len(handled_authors), 1)
        self.assertHandled(handled_authors, [self.authors[2]])