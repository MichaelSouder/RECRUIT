class Contrastsensitivity < ApplicationRecord
    self.table_name = 'contrast_sensitivity'

    belongs_to :subject
end
