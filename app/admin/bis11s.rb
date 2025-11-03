ActiveAdmin.register Bis11 do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :visit_num, :study_id, :bis_1, :bis_2, :bis_3, :bis_4, :bis_5, :bis_6, :bis_7, :bis_8, :bis_9, :bis_10, :bis_11, :bis_12, :bis_13, :bis_14, :bis_15, :bis_16, :bis_17, :bis_18, :bis_19, :bis_20, :bis_21, :bis_22, :bis_23, :bis_24, :bis_25, :bis_26, :bis_27, :bis_28, :bis_29, :bis_30, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :bis_1, :bis_2, :bis_3, :bis_4, :bis_5, :bis_6, :bis_7, :bis_8, :bis_9, :bis_10, :bis_11, :bis_12, :bis_13, :bis_14, :bis_15, :bis_16, :bis_17, :bis_18, :bis_19, :bis_20, :bis_21, :bis_22, :bis_23, :bis_24, :bis_25, :bis_26, :bis_27, :bis_28, :bis_29, :bis_30, :administrator, :verified_by]
  #   permitted << :other if params[:action] == 'create' && current_user.admin?
  #   permitted
  # end
  
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
  #filter :id
  #filter :subject_id
  #filter :date
  #filter :visit_num
  #filter :administrator
  #filter :verified_by

  form do |f|
    f.semantic_errors
    f.inputs  do    
      f.input :subject, :label => "Subject ID"
      f.input :date, :label => "Date (yyyy-mm-dd)", as: :datepicker,
      datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
      }
      f.input :visit_num
      f.input :study_id, :label => "Study ID"
      f.input :bis_1
      f.input :bis_2
      f.input :bis_3
      f.input :bis_4
      f.input :bis_5
      f.input :bis_6
      f.input :bis_7
      f.input :bis_8
      f.input :bis_9
      f.input :bis_10
      f.input :bis_11
      f.input :bis_12
      f.input :bis_13
      f.input :bis_14
      f.input :bis_15
      f.input :bis_16
      f.input :bis_17
      f.input :bis_18
      f.input :bis_19
      f.input :bis_20
      f.input :bis_21
      f.input :bis_22
      f.input :bis_23
      f.input :bis_24
      f.input :bis_25
      f.input :bis_26
      f.input :bis_27
      f.input :bis_28
      f.input :bis_29
      f.input :bis_30
      f.input :administrator
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons 
    end
end
