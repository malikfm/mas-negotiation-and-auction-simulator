from typing import List

import uvicorn
from fastapi import FastAPI, Request, Form
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from auction_repository import AuctionRepository
from auction_usecase import AuctionUsecase
from negotiation_repository import NegotiationRepository
from negotiation_usecase import NegotiationUsecase

app = FastAPI()
templates = Jinja2Templates(directory="./templates")
app.mount("/statics", StaticFiles(directory="./templates/statics"), name="statics")

negotiation_repository = NegotiationRepository()
negotiation_usecase = NegotiationUsecase(negotiation_repository)
auction_repository = AuctionRepository()
auction_usecase = AuctionUsecase(auction_repository)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/negotiations")
async def get_negotiations(request: Request):
    negotiations = negotiation_usecase.show_all_negotiations()
    return templates.TemplateResponse("negotiations.html", {"request": request, "negotiations": negotiations})


@app.get("/negotiation/new")
async def add_negotiation(request: Request):
    buyers = negotiation_usecase.get_all_buyers()
    bicycles = negotiation_usecase.get_all_bicycles()

    return templates.TemplateResponse(
        "new_negotiation.html",
        {"request": request, "buyers": buyers, "bicycles": bicycles}
    )


@app.post("/negotiation/new")
async def add_negotiation(buyer_ids: List[int] = Form(...), bicycle_ids: List[int] = Form(...)):
    negotiation_id = negotiation_usecase.simulate_negotiations(buyer_ids, bicycle_ids)

    return RedirectResponse(url=f"/negotiation/{negotiation_id}", status_code=303)


@app.get("/negotiation/{id}")
async def get_negotiation_history(id: str, request: Request):
    activity_log = negotiation_usecase.show_activity_log_per_negotiation(id)

    return templates.TemplateResponse(
        "negotiation_history.html",
        {"request": request, "negotiation_id": id, "activity_log": activity_log}
    )


@app.get("/auctions")
async def get_auctions(request: Request):
    auctions = auction_usecase.show_all_auctions()
    return templates.TemplateResponse("auctions.html", {"request": request, "auctions": auctions})


@app.get("/auction/new")
async def add_auction(request: Request):
    bidders = auction_usecase.get_all_bidders()
    items = auction_usecase.get_all_items()

    return templates.TemplateResponse(
        "new_auction.html",
        {"request": request, "bidders": bidders, "items": items}
    )


@app.post("/auction/new")
async def add_auction(bidder_ids: List[int] = Form(...), item_ids: List[int] = Form(...)):
    auction_id = auction_usecase.simulate_auctions(bidder_ids, item_ids)

    return RedirectResponse(url=f"/auction/{auction_id}", status_code=303)


@app.get("/auction/{id}")
async def get_auction_history(id: str, request: Request):
    activity_log = auction_usecase.show_activity_log_per_auction(id)

    return templates.TemplateResponse(
        "auction_history.html",
        {"request": request, "auction_id": id, "activity_log": activity_log}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
