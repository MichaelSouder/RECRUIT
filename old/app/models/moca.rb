class Moca < ApplicationRecord
    self.table_name = 'moca'
  
    belongs_to :subject
  
  end
  