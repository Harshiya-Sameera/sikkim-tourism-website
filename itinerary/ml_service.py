from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tourism.models import TouristPlace

def get_ml_recommendations(user_interests, top_n=10):
    # 1. Fetch all places and their descriptions
    places = TouristPlace.objects.all()
    descriptions = [p.description for p in places]
    
    # 2. Add user interest as the last item for comparison
    descriptions.append(user_interests)
    
    # 3. Vectorize the text
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(descriptions)
    
    # 4. Compare user interest (last row) with all places
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    
    # 5. Get top ranked indices
    related_indices = cosine_sim[0].argsort()[-top_n:][::-1]
    
    return [places[int(i)] for i in related_indices]