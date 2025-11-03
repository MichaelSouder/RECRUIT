ActiveAdmin.register Dotcounting do

permit_params :subject_id, :study_id, :date, :visit_num, :form, :trial_1to6_correct, :total_crrect, :administrator, :entered_by, :verified_by

index do
    id_column
    columnn :subject_id
    column :date
    column :study_id
    column :visit_num
    column :administrator
    actions
end

form do |f|
    f.semantic_errors
    f.inputs do
        f.input :date, :label => "Today's Date (yyyy-mm-dd)", as: :datepicker,
        datepicker_options: {
        min_date: "1900-01-01",
        max_date: "+3D"
        } 
        f.input :subject, :label => "Subject ID"
        f.input :study_id
        f.input :visit_num
        f.input :form
        f.input :trial_1to6_correct
        f.input :total_correct
        f.input :administrator
        f.input :entered_by
        f.input :verified_by
    end
    f.actions
end
end
    