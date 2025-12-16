class Nihsa < ApplicationRecord
    self.table_name = 'nih_neuro_qol_sa'

    belongs_to :subject
end
