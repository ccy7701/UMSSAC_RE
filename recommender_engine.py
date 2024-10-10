from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

def calculate_similarity(user_traits, other_traits):
    """
    Function to calculate similarity between the current user and another student.
    This can be expanded with more complex logic like cosine similarity, etc.
    """
    similarity = 1 - sum(abs(user_traits[key] - other_traits[key]) for key in user_traits.keys()) / len(user_traits)
    return similarity


@app.route('/recommendationEngine', methods=['POST'])
def recommend_partners():
    """
    This endpoint accepts the user's UserTraitsRecord, and that of other students,
    and returns recommended study partners based on similarity.
    """
    # Extract the current user's traits record
    own_record = request.json['user_traits_record']

    # Extract the other students' records
    other_students_records = request.json['other_students_traits_records']

    recommendations = []

    # Compare the current user against all other students
    for student in other_students_records:
        try:
            # Calculate similarity between WTC data
            similarity_wtc = calculate_similarity(own_record['wtc_data'], student['wtc_data'])

            # Calculate similarity between personality data
            similarity_personality = calculate_similarity(own_record['personality_data'], student['personality_data'])

            # Calculate similarity between skills data
            similarity_skills = calculate_similarity(own_record['skills_data'], student['skills_data'])

            # Average the similarity scores (you can change this logic to weight certain traits more)
            overall_similarity = (similarity_wtc + similarity_personality + similarity_skills) / 3

            # Append to the recommendation list
            recommendations.append({
                'profile_id': student['profile_id'],
                'similarity': overall_similarity
            })
        except Exception as e:
            # Handle any errors (such as missing keys, invalid data types, etc.)
            print(f"Error processing student {student['profile_id']}: {e}")
            continue  # Skip this student if there's an error

    # Sort by similarity (highest first)
    sorted_recommendations = sorted(recommendations, key=lambda x: float(x['similarity']), reverse=True)

    # Limit to top n = 10 recommendations
    top_recommendations = sorted_recommendations[:10]

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"({current_time}) Returning the top ten recommendations... ")

    return jsonify(top_recommendations)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
