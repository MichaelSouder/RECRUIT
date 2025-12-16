class Minilifetimesd < ApplicationRecord
    self.table_name = 'mini_lifetime_substance_disorders'
  
    belongs_to :subject
  
  end
  