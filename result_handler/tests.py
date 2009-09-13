from datetime import datetime

from django.db import models
from django.test import TestCase

from result_handler import ResultHandler, InsuficientColumnsException, InvalidQueryException

    
class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    dob = models.DateField()
    
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author)
    
class Coffee(models.Model):
    brand = models.CharField(max_length=255, db_column="name")
    
class Reviewer(models.Model):
    reviewed = models.ManyToManyField(Book)


class ResultHandlerTests(TestCase):
    
    def setUp(self):
        self.authors = []
        self.books = []
        self.coffees = []
        self.reviewers = []
        
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
        
        self.reviewers.append(Reviewer.objects.create())
        self.reviewers.append(Reviewer.objects.create())
        self.reviewers[0].reviewed.add(self.books[3])
        self.reviewers[0].reviewed.add(self.books[1])
        self.reviewers[0].reviewed.add(self.books[2])
        
    def assertSuccessfulHandling(self, model, query, expected_results, expected_annotations=(), params=[], translations=None):
        handled = ResultHandler(model, query, params, translations)
        self.assertHandled(handled, expected_results, expected_annotations)
        self.assertAnnotations(handled, expected_annotations)
        
        
    def assertHandled(self, handled, orig, expected_annotations=()):
        self.assertEqual(len(handled), len(orig))
        for index, item in enumerate(handled):
            orig_item = orig[index]
            for annotation in expected_annotations:
                setattr(orig_item, *annotation)
            
            self.assertEqual(item.id, orig_item.id)
            
    def assertNoAnnotations(self, handled):
        self.assertAnnotations(handled, ())
        
    def assertAnnotations(self, handled, expected_annotations):
        self.assertEqual(handled._annotations, expected_annotations)
        
    def testSimpleHandler(self):
        query = "SELECT * FROM result_handler_author"
        self.assertSuccessfulHandling(Author, query, self.authors)
        
    def testFkeyHandler(self):
        query = "SELECT * FROM result_handler_book"
        self.assertSuccessfulHandling(Book, query, self.books)
        
    def testDBColumnHandler(self):
        query = "SELECT * FROM result_handler_coffee"
        self.assertSuccessfulHandling(Coffee, query, self.coffees)
        
    def testOrderHandler(self):
        selects = (
            ('dob, last_name, first_name, id'),
            ('last_name, dob, first_name, id'),
            ('first_name, last_name, dob, id'),
        )
        
        for select in selects:
            query = "SELECT %s FROM result_handler_author" % select
            self.assertSuccessfulHandling(Author, query, self.authors)
            
    def testTranslations(self):
        query = "SELECT first_name AS first, last_name AS last, dob, id FROM result_handler_author"
        translations = (
            ('first', 'first_name'),
            ('last', 'last_name'),
        )
        self.assertSuccessfulHandling(Author, query, self.authors, translations=translations)
        
    def testParams(self):
        query = "SELECT * FROM result_handler_author WHERE first_name = %s"
        params = [self.authors[2].first_name]
        handled = ResultHandler(Author, query, params)
        self.assertHandled(handled, [self.authors[2]])
        self.assertNoAnnotations(handled)
        self.assertEqual(len(handled), 1)
        
    def testManyToMany(self):
        query = "SELECT * FROM result_handler_reviewer"
        self.assertSuccessfulHandling(Reviewer, query, self.reviewers)
        
    def testExtraConversions(self):
        query = "SELECT * FROM result_handler_author"
        translations = (('something', 'else'),)
        self.assertSuccessfulHandling(Author, query, self.authors, translations=translations)
        
    def testInsufficientColumns(self):
        query = "SELECT first_name, dob FROM result_handler_author"
        raised = False
        try:
            self.assertSuccessfulHandling(Author, query, self.authors)
        except InsuficientColumnsException:
            raised = True
            
        self.assertTrue(raised)
        
    def testAnnotations(self):
        query = "SELECT a.*, count(b.id) as book_count FROM result_handler_author a LEFT JOIN result_handler_book b ON a.id = b.author_id GROUP BY a.id, a.first_name, a.last_name, a.dob ORDER BY a.id"
        expected_annotations = (
            ('book_count', 3),
            ('book_count', 0),
            ('book_count', 1),
            ('book_count', 0),
        )
        self.assertSuccessfulHandling(Author, query, self.authors, expected_annotations)
        
    def testInvalidQuery(self):
        query = "UPDATE result_handler_author SET first_name='thing' WHERE first_name='Joe'"
        self.assertRaises(InvalidQueryException, ResultHandler, Author, query)
            