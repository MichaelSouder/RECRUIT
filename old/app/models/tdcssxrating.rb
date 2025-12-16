class Tdcssxrating < ApplicationRecord
    self.table_name = 'tdcs_symptom_ratings'
  
    belongs_to :subject
  
  end
  