class Handedness < ApplicationRecord
    self.table_name = 'handedness'
  
    belongs_to :subject
  end
  