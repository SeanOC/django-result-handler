from django.db import connection

class ResultHandler(object):
    
    def __init__(self, model, query, params=[], translations=None):
        # setup instance info
        self.cursor = connection.cursor()
        self.cursor.execute(query, params)
        self.model = model
        
        # Figure out the column names
        self.fields = [column[0] for column in self.cursor.description]
        # Adjust any column names which don't match field names
        if translations is not None:
            for translation in translations:
                try:
                    index = fields.index(translation[0])
                    self.fields[index] = translation[1]
                except ValueError:
                    # Ignore transations for non-existant column names
                    pass
        
        # Build a list of column names known by the model
        self.model_fields = [field.column for field in model._meta.fields]
        
        
    def __iter__(self):
        values = cursor.fetchone()
        
    def _transform_result(self, result):
        pass