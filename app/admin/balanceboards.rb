ActiveAdmin.register Balanceboard do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :visit_num, :study_id, :agilisway_num, :task_code, :task, :ap, :ml, :character_finished, :character_count, :paragraph_passes, :comments, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :agilisway_num, :task_code, :task, :ap, :ml, :character_finished, :character_count, :paragraph_passes, :comments, :administrator, :verified_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  
  index do
    id_column
    column :subject
    column :date
    column :visit_num
    column :study_id
    column :task_code
    column :task
    column :administrator
    column :verified_by
    actions
  end

  form do |f|
  f.semantic_errors
  f.inputs  do    
    f.input :subject, :label => "Subject ID"
    f.input :date, :label => "Today's Date (yyyy-mm-dd)", as: :datepicker,
    datepicker_options: {
      min_date: "1900-01-01",
      max_date: "+3D"
    }  
    f.input :visit_num
    f.input :study_id, :label => "Study ID"
    f.input :agilisway_num
    f.input :task_code
    f.input :task
    f.input :ap
    f.input :ml
    f.input :character_finished
    f.input :character_count
    f.input :paragraph_passes
    f.input :comments
    f.input :administrator
    f.input :verified_by
  end
  f.actions         # adds the 'Submit' and 'Cancel' buttons 
  end
end