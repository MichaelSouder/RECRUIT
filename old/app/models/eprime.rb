class Eprime < ApplicationRecord
    self.table_name = 'eprime_id'
  
    belongs_to :subject
  
  end
  