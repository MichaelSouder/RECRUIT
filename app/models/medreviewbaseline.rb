class Medreviewbaseline < ApplicationRecord
    self.table_name = 'medications_review_baseline'
  
    belongs_to :subject
  
  end
  