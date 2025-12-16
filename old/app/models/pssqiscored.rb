class Pssqiscored < ApplicationRecord
  self.table_name = 'pssqi_scored'
  
  belongs_to :subject 
  #belongs_to :subject  # from a different database dvbic_pmr, also 60K entries
  # gave an odd object entry <x#abn2e etc.
end
