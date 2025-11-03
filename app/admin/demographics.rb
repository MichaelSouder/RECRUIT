ActiveAdmin.register Demographic do

require 'date'
  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :study_id, :sex, :date_of_birth, :race, :status, :service_branch, :period_of_service, :education_level, :administrator, :verified_by, :time_stamp
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :study_id, :sex, :date_of_birth, :race, :status, :service_branch, :period_of_service, :education_level, :time_stamp, :administrator, :verified_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
index do
  id_column
  column :subject_id
  column :date
  column :study_id
  column :sex
  column :date_of_birth
  column :administrator
  column :verified_by
  actions 
end
#  filter :subject_id
#  filter :study_id
#  filter :date
#  filter :status
#  filter :administrator
#  filter :date_of_birth

form do |f|
  f.semantic_errors
  f.inputs  do    
    f.input :date, :label => "Today's Date (yyyy-mm-dd)", as: :datepicker,
    datepicker_options: {
      min_date: "1900-01-01",
      max_date: "+3D"
    } 
    f.input :subject, :label => "Subject ID"
    f.input :study_id
    f.input :sex
    #f.input :date_of_birth, :as => :date_select
    f.input :date_of_birth, :label => "Date of Birth (yyyy-mm-dd)",
              as: :datepicker,
                    datepicker_options: {
                      min_date: "1900-01-01",
                      max_date: "+3D"
                    } 
    f.input :race
    f.input :status
    f.input :service_branch
    f.input :period_of_service
    f.input :education_level
    f.input :administrator
    f.input :verified_by
    f.input :time_stamp, as: :datetime_picker
  end
  f.actions         # adds the 'Submit' and 'Cancel' buttons 
end
end