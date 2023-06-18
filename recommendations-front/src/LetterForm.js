import React from 'react';
import './LetterForm.css'; // Import the CSS file

class LetterForm extends React.Component {
  state = {
    letter: '',
    prediction: '',
    issues: [],
    submitted: false,
    score: 0,
  };

  handleInputChange = (event) => {
    this.setState({
      letter: event.target.value,
    });
  };

  handleSubmit = (event) => {
    event.preventDefault();
    fetch('http://localhost:8000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        userLetter: this.state.letter,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Data object:', data);
        this.setState({
          prediction: data.prediction,
          issues: data.issues,
          score: data.quality_score,
          submitted: true,
        });
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  render() {
    return (
      <div className='container'>
        {!this.state.submitted ? (
          <form onSubmit={this.handleSubmit}>
            <label>
              Enter your letter:
              <textarea
                className='textarea'
                value={this.state.letter}
                onChange={this.handleInputChange}
              />
            </label>
            <button type='submit' className='submit-button'>
              Submit
            </button>
          </form>
        ) : (
          <div className='result'>
            <h2 className='subheader'>Your motivational letter score:</h2>

            {this.state.prediction === 'ideal' ? (
              <React.Fragment>
                <div className='circle'>
                  <div
                    className='circle-bar'
                    style={{
                      background:
                        'conic-gradient(#4c7eb8 0% ' +
                        this.state.score +
                        '%, lightgray ' +
                        this.state.score +
                        '% 100%)',
                    }}
                  ></div>
                  <div className='circle-text'>
                    {Math.round(this.state.score)}%
                  </div>
                </div>
                <p className='score'>{Math.round(this.state.score)}%</p>
                <p className='motivational'>
                  Your letter is great! Keep it up!
                </p>
              </React.Fragment>
            ) : (
              <div className='improvement text-result'>
                <p>
                  Keep on working on your letter, you still have some things to
                  improve.
                </p>
                <p className='issues text-result'>
                  Fix Following Issues: {this.state.issues.join(', ')}
                </p>
              </div>
            )}

            <button
              onClick={() => this.setState({ submitted: false, letter: '' })}
              className='new-letter-button'
            >
              Enter a New Letter
            </button>
          </div>
        )}
      </div>
    );
  }
}

export default LetterForm;
