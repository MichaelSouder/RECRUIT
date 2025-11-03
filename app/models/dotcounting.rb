class Dotcounting < ApplicationRecord
    self.table_name = 'dot_counting'

    belongs_to :subject
end
