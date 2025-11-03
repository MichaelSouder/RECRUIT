ActiveAdmin.register Stafftraining do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :first_name, :last_name, :study_id, :training, :training_date, :cleared, :expiration_date, :trainer, :comments
  #
  # or
  #
  # permit_params do
  #   permitted = [:first_name, :last_name, :study_id, :training, :training_date, :cleared, :expiration_date, :trainer, :comments]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  form do |f|
    f.semantic_errors
    f.inputs  do    
      f.input :first_name
      f.input :last_name
      f.input :study_id
      f.input :training
      f.input :training_date, as: :datepicker, 
      datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
      }
      f.input :cleared
      f.input :expiration_date, as: :datepicker, 
      datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
      }
      f.input :trainer
      f.input :comments
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons
  end
  
  index do
    id_column
    column :first_name
    column :last_name
    column :study_id
    column :training
    column :training_date
    column :trainer
    column :comments
    actions
  end 

  # specify filters
  # filter :id
  # filter :study_id
  # filter :first_name
  # filter :last_name
  # filter :training
  # filter :training_date
  # filter :trainer
end
