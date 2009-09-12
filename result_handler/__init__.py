from django.db import connection

class ResultHandler(object):
    
    def __init__(self, model, query, params=[], translations=None):
        # setup instance info
        self.cursor = connection.cursor()
        self.cursor.execute(query, params)
        self.model = model
        
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
        kwargs = {}
        annotations = ()
        
        # Associate fields to values
        for pos, value in enumerate(values):
            column = self.columns[pos]
            
            # Separate properties from annotations
            if column in self.model_fields.keys():
                kwargs[self.model_fields[column]] = value
            else:
                annotations += (column, value),
                
        # Construct model instance
        instance = self.model(**kwargs)
        
        # Apply annotations
        for field, value in annotations:
            setattr(instance, field, value)
            
        return instance