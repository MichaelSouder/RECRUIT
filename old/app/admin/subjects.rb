ActiveAdmin.register Subject do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #

  permit_params :id, :first_name, :middle_name, :last_name, :date_of_birth, :sex, :ssn, :race, :death_date, :county, :zip, :created_by
  

  form do |f|
    f.semantic_errors
    f.inputs  do
      f.input :first_name
      f.input :last_name
      f.input :sex, :as => :select, :collection => [["male", 0],
                                                    ["female",1]]
      #f.input :date_of_birth, :as => :date_select
      f.input :date_of_birth, :label => "Date of Birth (yyyy-mm-dd)",
                as: :datepicker,
                      datepicker_options: {
                        min_date: "1900-01-01",
                        max_date: "+3D"
                      } 
      f.input :ssn, :label => "SSN (xxx-xx-xxxx)"
      f.input :race
      f.input :death_date, :label => "Date of Death (yyyy-mm-dd)",
                as: :datepicker,
                      datepicker_options: {
                        min_date: "1900-01-01",
                        max_date: "+3D"
                      } 
      f.input :zip
      f.input :created_by
      
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons
  end

  index do
    id_column
    column :first_name
    column :last_name
    column :date_of_birth
    column :sex
    column :ssn
    column :created_by
    actions
  end 

  filter :id
  filter :first_name
  filter :last_name
  filter :date_of_birth
  filter :sex
  filter :ssn
  filter :race
  filter :zip
  filter :created_by
end
