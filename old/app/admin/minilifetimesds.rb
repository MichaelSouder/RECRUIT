ActiveAdmin.register Minilifetimesd do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :visit_num, :study_id, :lifetime_alcohol_dependence, :lifetime_alcohol_abuse, :lifetime_substance_dependence, :dependence_substances_used, :lifetime_substance_abuse, :abuse_substances_used, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :lifetime_alcohol_dependence, :lifetime_alcohol_abuse, :lifetime_substance_dependence, :dependence_substances_used, :lifetime_substance_abuse, :abuse_substances_used, :administrator, :verified_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end

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
      f.input :visit_num
      f.input :lifetime_alcohol_dependence
      f.input :lifetime_alcohol_abuse
      f.input :lifetime_substance_dependence
      f.input :dependence_substances_used
      f.input :lifetime_substance_abuse
      f.input :abuse_substances_used
      f.input :administrator
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons
  end
  
  index do
    id_column
    column :subject
    column :date
    column :visit_num
    column :study_id
    column :administrator
    column :verified_by
    actions
  end 

  # specify filters
  # filter :id
  # filter :subject
  # filter :date
  # filter :visit_num
  # filter :administrator
  # filter :verified_by
  
end

