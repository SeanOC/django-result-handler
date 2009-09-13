from django.db import connection

class InsuficientColumnsException(Exception):
    """
    The query passed to raw doesn't include all of the columns needed to build 
    a model instance.
    """
    pass
    
class InvalidQueryException(Exception):
    """
    The query passed to raw isn't a safe query to use with raw.
    """
    pass

class ResultHandler(object):
    
    def __init__(self, model, query, params=[], translations=None):
        # setup instance info
        self.validate_query(query)
        
        self.cursor = connection.cursor()
        self.cursor.execute(query, params)
        self.model = model
        self._kwargs = {}
        self._annotations = ()
        # Figure out the column names
        self.columns = [column_meta[0] for column_meta in self.cursor.description]
        # Adjust any column names which don't match field names
        if translations is not None:
            for translation in translations:
                try:
                    index = self.columns.index(translation[0])
                    self.columns[index] = translation[1]
                except ValueError:
                    # Ignore transations for non-existant column names
                    pass
        
        # Build a list of column names known by the model
        self.model_fields = {}
        for field in model._meta.fields:
            name, column = field.get_attname_column()
            self.model_fields[column] = name
        
    def __iter__(self):
        values = self.cursor.fetchone()
        while values:
            yield self._transform_result(values)
            values = self.cursor.fetchone()
            
    def __len__(self):
        return self.cursor.rowcount
        
    def _transform_result(self, values):
        kwargs = self._kwargs
        annotations = self._annotations
        
        # Associate fields to values
        for pos, value in enumerate(values):
            column = self.columns[pos]
            
            # Separate properties from annotations
            if column in self.model_fields.keys():
                kwargs[self.model_fields[column]] = value
            else:
                annotations += (column, value),
                
        if len(kwargs) < len(self.model_fields):
            missing = [column for column, field in self.model_fields.items() if field not in kwargs.keys()]
            raise InsuficientColumnsException("They query passed doesn't contain all of the needed columns.  The missing columns are: %s" % ', '.join(missing))
            
        # Construct model instance
        instance = self.model(**kwargs)
        
        # Apply annotations
        for field, value in annotations:
            setattr(instance, field, value)
        
        # make the kwargs and annotation metadata available to the unit tests
        self._kwargs = kwargs
        self._annotations = annotations
        return instance
    
    def validate_query(self, query):
        if not query.lower().startswith('select'):
            raise InvalidQueryException('Raw only handles select queries.')