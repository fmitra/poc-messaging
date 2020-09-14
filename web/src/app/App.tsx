import { h, Component } from 'preact';

import Connect from '@messaging/components/Connect';

export default class App extends Component {
  render(): JSX.Element {
    return (
      <div class='app'>
        <Connect />
      </div>
    );
  }
};
