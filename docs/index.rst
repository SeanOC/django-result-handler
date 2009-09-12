=====================
django-result-handler
=====================

ResultHandler is a utility class to help turn the results of raw database queries into Django model instances.

Basic Use
=========

Example of basic use:

    import ResultHandler
    from library import Author, Book

    # Basic use
    query = "select id, first_name, last_name from library_author"
    authors = ResultHandler(Author, query)

    # Extended use
    query = """select id, first_name as first, last_name as last, count(select * from library_book...) as book_count 
               from library_author where first ilike %s and last ilike %s"""
    params = ('John', 'Doe')
    translations = (
        ('first', 'first_name'),
        ('last', 'last_name'),
    )                
    authors = ResultHandler(Author, query, params, translations)
    