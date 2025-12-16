class Bssi < ApplicationRecord
    self.table_name = 'bssi'
  
    belongs_to :subject
  
  end
  