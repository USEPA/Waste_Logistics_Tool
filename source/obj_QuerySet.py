import arcpy,os

###############################################################################
class QuerySet:

   #...........................................................................
   def __init__(self
      ,queryset
   ):
      #////////////////////////////////////////////////////////////////////////
      self.queryset             = queryset;
      self.flds                 = [];
      self.lkup                 = {};
      #////////////////////////////////////////////////////////////////////////
      
      idx = 0;
      for key,val in self.queryset.items():
         if val is not None and val != "" and val != " ":
            self.flds.append(val);
            self.lkup[key] = idx;
            idx += 1;
   
   #...........................................................................
   def idx(self,row,col):
      
      if col is None or col not in self.lkup:
         return None;
         
      else:
         return row[self.lkup[col]];
         
   #...........................................................................
   def idx_clean_double(self,row,col):
   
      if col is None or col not in self.lkup:
         return None;
         
      else:
         value = row[self.lkup[col]];
         
         if value is None:
            return None;

         if str(value) == "":
            return None;

         try:
            v = float(value);

         except ValueError:
            v = None;

         return v;
         
   #...........................................................................
   def idx_clean_int(self,row,col):
   
      if col is None or col not in self.lkup:
         return None;
         
      else:
         value = row[self.lkup[col]];
         
         if value is None:
            return None;

         if str(value) == "":
            return None;

         try:
            v = int(value);

         except ValueError:
            v = None;

         return v;

   #...........................................................................
   def idx_clean_boo(self,row,col):
   
      if col is None or col not in self.lkup:
         return None;
         
      else:
         value = row[self.lkup[col]];
         
         if value is None:
            return None;

         if str(value) == "":
            return None;

         if str(value) in ["-1","1","TRUE","True","true","Y","y","Yes","YES"]:
            return 'True';

         if str(value) in ["0","FALSE","False","false","N","n","No","NO"]:
            return 'False';

         return None;
   
   #...........................................................................
   def idx_clean_string(self,row,col):

      if col is None or col not in self.lkup:
         return None;
         
      else:
         value = row[self.lkup[col]];
         
         if value is None:
            return None;

         if str(value) == "":
            return None;
            
         return str(value);
         
      