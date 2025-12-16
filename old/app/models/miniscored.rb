class Miniscored < ApplicationRecord
    self.table_name = 'mini_scored'
  
    belongs_to :subject
  
  end
  