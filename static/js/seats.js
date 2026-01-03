let selectedSeats = [];
let pricePerSeat = 200;

function toggleSeat(btn) {
  const seat = btn.dataset.seat;

  if (selectedSeats.includes(seat)) {
    selectedSeats = selectedSeats.filter(s => s !== seat);
    btn.classList.remove("selected");
  } else {
    selectedSeats.push(seat);
    btn.classList.add("selected");
  }

  document.getElementById("count").innerText = selectedSeats.length;
  document.getElementById("total").innerText =
    selectedSeats.length * pricePerSeat;
}

function continueBooking(showId) {
  if (selectedSeats.length === 0) {
    alert("Please select at least one seat");
    return;
  }

  fetch("/lock_seats", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      show_id: showId,
      seats: selectedSeats
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === "ok") {
      window.location.href = "/otp";
    } else {
      alert("Some seats are no longer available");
      window.location.reload();
    }
  });
}
