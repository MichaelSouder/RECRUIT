class Mnbestconsensussummary < ApplicationRecord
    self.table_name = 'mnbest_consensus_test'
    #self.primary_key = 'id'
    belongs_to :subject
  end