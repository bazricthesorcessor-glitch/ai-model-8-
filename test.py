from router.model_selector import select_model

model = select_model(
    "can you please write a 1000 words essay"
)

print(model)
