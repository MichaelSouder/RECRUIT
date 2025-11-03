class Nihwb < ApplicationRecord
    self.table_name = 'nih_neuro_qol_wb'

    belongs_to :subject
end
