import stockanalysis as sa

aapl = sa.stock("AAPL")

df = aapl.transcripts()
first_id = df["id"].iloc[0]
lt = aapl.transcript(first_id)

print("title:", lt["title"])
print(f"\nturns: {len(lt['turns'])}")
print("First turn:", lt["turns"][0])
print("Last turn:", lt["turns"][-1])


