ActiveAdmin.register Study do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :irb_number, :description, :note, :investigator, :status, :start_date, :end_date, :created_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:irb_number, :description, :note, :investigator, :status, :start_date, :end_date, :created_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  form do |f|
    f.semantic_errors
    f.inputs  do    
      f.input :irb_number
      f.input :description
      f.input :note
      f.input :investigator
      f.input :status
      f.input :start_date, as: :datepicker, 
      datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
      }
      f.input :end_date, as: :datepicker, 
      datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
      }
      f.input :created_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons
  end
  
end
