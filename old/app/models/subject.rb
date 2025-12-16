class Subject < ActiveRecord::Base
  # establish_connection(:dvbicpmr)
  self.table_name = "subjects"

  #def to_label
  #  "#{name} #{id}"
  #end

  # https://stackoverflow.com/questions/8429555/how-to-show-model-title-instead-on-mymodel0x000000-in-activeadmin-dropdow
  def name
    return "#{self.id}: #{self.last_name}, #{self.first_name}"
  end

  #alias_attribute :to_label, :name

end
