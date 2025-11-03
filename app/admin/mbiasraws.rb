ActiveAdmin.register Mbiasraw do

  # See permitted parameters documentation:
  # https://github.com/activeadmin/activeadmin/blob/master/docs/2-resource-customization.md#setting-up-strong-parameters
  #
  # Uncomment all parameters which should be permitted for assignment
  #
  permit_params :subject_id, :date, :visit_num, :study_id, :mbias_1, :mbias_2, :mbias_3, :mbias_4, :mbias_5, :mbias_6, :mbias_7, :mbias_8, :mbias_9, :mbias_10, :mbias_11, :mbias_12, :mbias_13, :mbias_14, :mbias_15, :mbias_16, :mbias_17, :mbias_18, :mbias_19, :mbias_20, :mbias_21, :mbias_22, :mbias_23, :mbias_24, :mbias_25, :mbias_26, :mbias_27, :mbias_28, :mbias_29, :mbias_30, :mbias_31, :mbias_32, :mbias_33, :mbias_34, :mbias_35, :mbias_36, :mbias_37, :mbias_38, :mbias_39, :mbias_40, :mbias_41, :mbias_42, :mbias_43, :mbias_44, :administrator, :verified_by
  #
  # or
  #
  # permit_params do
  #   permitted = [:subject_id, :date, :visit_num, :study_id, :mbias_1, :mbias_2, :mbias_3, :mbias_4, :mbias_5, :mbias_6, :mbias_7, :mbias_8, :mbias_9, :mbias_10, :mbias_11, :mbias_12, :mbias_13, :mbias_14, :mbias_15, :mbias_16, :mbias_17, :mbias_18, :mbias_19, :mbias_20, :mbias_21, :mbias_22, :mbias_23, :mbias_24, :mbias_25, :mbias_26, :mbias_27, :mbias_28, :mbias_29, :mbias_30, :mbias_31, :mbias_32, :mbias_33, :mbias_34, :mbias_35, :mbias_36, :mbias_37, :mbias_38, :mbias_39, :mbias_40, :mbias_41, :mbias_42, :mbias_43, :mbias_44, :administrator, :verified_by]
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
  end

  #filter :subject_id
  #filter :study_id
  #filter :visit_num
  #filter :date
  #filter :administrator

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
      f.input :mbias_1
      f.input :mbias_2
      f.input :mbias_3
      f.input :mbias_4
      f.input :mbias_5
      f.input :mbias_6
      f.input :mbias_7
      f.input :mbias_8
      f.input :mbias_9
      f.input :mbias_10
      f.input :mbias_11
      f.input :mbias_12
      f.input :mbias_13
      f.input :mbias_14
      f.input :mbias_15
      f.input :mbias_16
      f.input :mbias_17
      f.input :mbias_18
      f.input :mbias_19
      f.input :mbias_20
      f.input :mbias_21
      f.input :mbias_22
      f.input :mbias_23
      f.input :mbias_24
      f.input :mbias_25
      f.input :mbias_26
      f.input :mbias_27
      f.input :mbias_28
      f.input :mbias_29
      f.input :mbias_30
      f.input :mbias_31
      f.input :mbias_32
      f.input :mbias_33
      f.input :mbias_34
      f.input :mbias_35
      f.input :mbias_36
      f.input :mbias_37
      f.input :mbias_38
      f.input :mbias_39
      f.input :mbias_40
      f.input :mbias_41
      f.input :mbias_42
      f.input :mbias_43
      f.input :mbias_44
      f.input :administrator
      f.input :verified_by
    end
    f.actions         # adds the 'Submit' and 'Cancel' buttons 
    end
end