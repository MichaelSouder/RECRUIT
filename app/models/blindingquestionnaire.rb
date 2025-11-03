class Blindingquestionnaire < ApplicationRecord
    self.table_name = 'blinding_questionnaire'
  
    belongs_to :subject
  
  end
  