# code to get all the subject ids we have used in the data tables

def getuniq_id(obj, allids)
    ids = []
    obj.find_each do |item|
        ids.append(item.subject_id)
        allids.append(item.subject_id)
    end
    return ids.uniq.length()
end

puts "Total number of subjects: #{Subject.count}"

# cycle through all the subjects
ids = []
Subject.find_each do |subject|
    #puts "#{subject.id}"
    ids.append(subject.id)
end

puts "Length is: #{ids.length()}"

ids = []
Hit6.find_each do |hit|
    ids.append(hit.subject_id)
end
puts "Uniq: #{ids.uniq.length()}"

allids = []

array = [Ahrs, Asrm, Auditc, Aware, Bai, Balanceboard, Bicro, Bis11, 
    Bicroscored, Bisbas, Dass21, Hit6, Mpai,Pssqi]
array.map do |item|
    puts "#{item} #{item.count}"
    puts "  uniq #{getuniq_id(item, allids)}"
end

puts "All uniq ids: #{allids.uniq.length()}"

# sample code for executing sql code
# records_array = ActiveRecord::Base.connection.execute(sql)
# lets get the maximum value from id of bicro_scored
sql = "select max(id) from bicro_scored ;"
maxid = ActiveRecord::Base.connection.execute(sql)[0]['max']
puts "Maxid in bicro_scored is #{maxid}"
