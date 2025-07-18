# # gadget_search_engine/app/predictor.py

# import pandas as pd
# import numpy as np
# import faiss
# from sentence_transformers import SentenceTransformer

# class GadgetSearch:
#     def __init__(self, model_path_prefix="models/"):
#         """
#         Loads the FAISS index, gadget data, and the sentence transformer model.
#         """
#         print("Loading search engine...")
#         try:
#             # Load the FAISS index
#             self.index = faiss.read_index(f"{model_path_prefix}gadgets.faiss")
            
#             # Load the gadget data
#             self.df = pd.read_csv(f"{model_path_prefix}gadget_data.csv")
            
#             # Load the sentence transformer model
#             self.model = SentenceTransformer("all-MiniLM-L6-v2")
#             print("✅ Search engine loaded successfully.")
#         except (FileNotFoundError, faiss.FaissException) as e:
#             print(f"❌ Error loading models: {e}")
#             print("Please run the builder script first: python app/builder.py")
#             raise

#     def search(self, query, k=5):
#         """
#         Searches for gadgets based on a text query.

#         Args:
#             query (str): The user's description of the function.
#             k (int): The number of top results to return.

#         Returns:
#             list: A list of dictionaries, each containing the gadget name and similarity score.
#         """
#         # 1. Encode the query into a vector and normalize it
#         query_vector = self.model.encode([query])
#         faiss.normalize_L2(query_vector)

#         # 2. Search the FAISS index
#         # The 'search' method returns distances (scores) and indices
#         scores, indices = self.index.search(query_vector, k)

#         # 3. Format the results
#         results = []
#         for score, idx in zip(scores[0], indices[0]):
#             # The index might return -1 if there are fewer items than k
#             if idx != -1:
#                 results.append({
#                     "gadget_name": self.df.iloc[idx]['gadget_name'],
#                     "function": self.df.iloc[idx]['function'],
#                     "similarity": float(score)
#                 })
        
#         return results



# gadget_search_engine/app/predictor.py

import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class GadgetSearch:
    def __init__(self, model_path_prefix="models/"):
        """
        Loads the FAISS index, gadget data, and the sentence transformer model.
        """
        print("Loading search engine...")
        try:
            self.index = faiss.read_index(f"{model_path_prefix}gadgets.faiss")
            self.df = pd.read_csv(f"{model_path_prefix}gadget_data.csv")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✅ Search engine loaded successfully.")
        except (FileNotFoundError, faiss.FaissException) as e:
            print(f"❌ Error loading models: {e}")
            print("Please run the builder script first: `python app/builder.py`")
            raise

    def search(self, query, k=5):
        """
        Searches for gadgets, de-duplicates the results, and returns the top unique gadgets.

        Args:
            query (str): The user's description of the function.
            k (int): The number of top unique results to return.

        Returns:
            list: A list of unique dictionaries, each containing the gadget name, its best-matching
                  function, and the highest similarity score.
        """
        # --- START OF FIX ---

        # 1. Fetch a larger pool of candidates from FAISS.
        # Since multiple results can belong to the same gadget, we need to fetch more
        # than `k` items to ensure we find `k` unique gadgets.
        candidate_pool_size = k * 5  # Fetch 5x the number of desired results
        
        # 2. Encode the query and search the index.
        query_vector = self.model.encode([query])
        faiss.normalize_L2(query_vector)
        scores, indices = self.index.search(query_vector, candidate_pool_size)

        # 3. De-duplicate the results.
        # We will iterate through the results and only keep the first (and therefore highest-scoring)
        # entry for each unique gadget name.
        unique_results = []
        seen_gadget_names = set()

        for score, idx in zip(scores[0], indices[0]):
            # Stop if we have found enough unique results
            if len(unique_results) >= k:
                break
            
            # The index might return -1 if there are fewer items than the pool size
            if idx != -1:
                gadget_name = self.df.iloc[idx]['gadget_name']
                
                # If we haven't seen this gadget before, add it to our results.
                if gadget_name not in seen_gadget_names:
                    unique_results.append({
                        "gadget_name": gadget_name,
                        "function": self.df.iloc[idx]['function'], # The function with the best score
                        "similarity": float(score)
                    })
                    # Add the gadget name to our set of seen gadgets.
                    seen_gadget_names.add(gadget_name)
        
        return unique_results
        # --- END OF FIX ---