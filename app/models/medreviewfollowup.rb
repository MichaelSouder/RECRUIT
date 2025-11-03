class Medreviewfollowup < ApplicationRecord
    self.table_name = 'medications_review_followup'
  
    belongs_to :subject
  
  end
  