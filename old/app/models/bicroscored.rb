class Bicroscored < ApplicationRecord
    self.table_name = 'bicro_scored'

    # how to change id to be a primary key
    # ALTER TABLE bicro_scored ADD PRIMARY KEY (id);

    # change int to serial
    # https://cornercase.info/change-existing-column-to-serial-in-postgres/
    
end