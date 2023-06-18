import React from 'react';
import './LetterForm.css'; // Import the CSS file

class LetterForm extends React.Component {
  state = {
    letter: '',
    prediction: '',
    issues: [],
    submitted: false,
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
      .then((response) => {
        console.log(response);
        return response.json();
      })

      .then((data) => {
        console.log('Data object:', data);
        this.setState({
          prediction: data.prediction,
          issues: data.issues,
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
        {this.state.submitted && (
          <div className='result'>
            {this.state.issues.length === 0 ? (
              <p className='motivational'>
                Your letter is great! Never stop on!
              </p>
            ) : (
              <div className='improvement'>
                <p>
                  Keep on working on your letter: you still have some things to
                  improve:
                </p>
                <p className='issues'>Issues: {this.state.issues.join(', ')}</p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }
}

export default LetterForm;
