class Nihem < ApplicationRecord
    self.table_name = 'nih_neuro_qol_em'

    belongs_to :subject
end