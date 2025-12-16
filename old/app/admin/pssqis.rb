ActiveAdmin.register Pssqi do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject, :date, :visit_num, :study_id, :pssqi_1, :pssqi_1a, :pssqi_2, :pssqi_2a, :pssqi_3, :pssqi_3a, :pssqi_4, :pssqi_4a, :pssqi_5, :pssqi_5a, :pssqi_6, :pssqi_7, :pssqi_8, :pssqi_9, :pssqi_10, :pssqi_11, :pssqi_12, :pssqi_13, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :pssqi_1, :pssqi_1a, :pssqi_2, :pssqi_2a, :pssqi_3, :pssqi_3a, :pssqi_4, :pssqi_4a, :pssqi_5, :pssqi_5a, :pssqi_6, :pssqi_7, :pssqi_8, :pssqi_9, :pssqi_10, :pssqi_11, :pssqi_12, :pssqi_13, :administrator, :verified_by]
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
      f.input :pssqi_1
      f.input :pssqi_1a
      f.input :pssqi_2
      f.input :pssqi_2a
      f.input :pssqi_3
      f.input :pssqi_3a
      f.input :pssqi_4
      f.input :pssqi_4a
      f.input :pssqi_5
      f.input :pssqi_5a
      f.input :pssqi_6
      f.input :pssqi_7
      f.input :pssqi_8
      f.input :pssqi_9
      f.input :pssqi_10
      f.input :pssqi_11
      f.input :pssqi_12
      f.input :pssqi_13
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
  

  form do |f|
    f.semantic_errors
   
    f.inputs  do
      f.input :subject_id
      f.input :date, as: :datepicker
      f.input :visit_num
      f.input :study_id
      f.input :pssqi_1
      f.input :pssqi_1a
      f.input :pssqi_2
      f.input :pssqi_2a
      f.input :pssqi_3
      f.input :pssqi_3a
      f.input :pssqi_4
      f.input :pssqi_4a
      f.input :pssqi_5
      f.input :pssqi_5a
      f.input :pssqi_6
      f.input :pssqi_7
      f.input :pssqi_8
      f.input :pssqi_9
      f.input :pssqi_10
      f.input :pssqi_11
      f.input :pssqi_12
      f.input :pssqi_13
      f.input :administrator
      f.input :verified_by
      
    end

    f.actions
  end

end
