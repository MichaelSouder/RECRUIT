class Nihcog < ApplicationRecord
    self.table_name = 'nih_neuro_qol_cog'
  
    belongs_to :subject
  
  end
  