class Mnbestconsensus < ApplicationRecord
    self.table_name = 'mnbest_consensus_summary'
  
    belongs_to :subject
  
  end
  