class Balanceboard < ApplicationRecord
    self.table_name = 'balance_board'

    belongs_to :subject
end